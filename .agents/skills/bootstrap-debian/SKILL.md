---
name: bootstrap-debian
description: Bootstrap a fresh Debian server for a GitHub user: create their sudo user with their GitHub SSH keys and git identity, rotate root and user passwords, disable root and password SSH login, and restrict the firewall to 22/80/443 tcp. Use when the user asks to set up, provision, bootstrap, or harden a new Debian server or VPS.
---

# Bootstrap a Debian server

Agentic runbook: run the shell commands yourself over SSH, verify each stage, and report the generated credentials. Do not hand the user a script to run unless they ask for one.

Fixed outcomes unless the user overrides them:

- New sudo user named after the GitHub username, passwordless sudo
- Git identity for that user from their public GitHub data
- New strong random passphrases for `root` and the new user (24 words chosen with `secrets.choice` from the BIP39 English word list)
- sshd: no root login, no password/keyboard-interactive login, keys only
- Firewall (nftables): inbound `22,80,443/tcp` and ICMP/ICMPv6 only, everything else dropped

## Inputs

Ask for anything missing before touching the server. Required:

1. **GitHub username**
2. **Server hostname** (or IP)
3. **Initial SSH access**: `root` password, or an existing login (user + key/password/sudo) that can reach root

Derived, confirm only if they do not fit:

- Login name = GitHub username. It must be a valid Unix name (`^[a-z_][a-z0-9_-]*$`, ≤32 chars); if not, ask what login name to use.
- Git name/email: resolved from GitHub (see step 1); report what was chosen.

Warn once before starting: root/password login will be disabled, so a bad `authorized_keys` can lock everyone out. The ordering below (create and verify the user *before* hardening sshd) is the protection — never reorder it.

## Safety rules

- Never write passwords, private keys, or filled setup scripts into a git-tracked file. Keep secrets only in a local temp file with mode `0600`, delete it at the end, and show the new passwords once in the final report.
- Generate each password as a 24-word passphrase with a CSPRNG, choosing each word with `secrets.choice` from the BIP39 English word list bundled at `references/bip39-english.txt` (relative to this skill; [BIP-39 `english.txt`](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt)). These are diceware-style passphrases, not checksummed BIP39 mnemonics — do not use them as wallet seeds. From the repo root:

  ```sh
  python3 -c 'from pathlib import Path; import secrets; words=Path(".agents/skills/bootstrap-debian/references/bip39-english.txt").read_text(encoding="utf-8").split(); assert len(words)==2048; print(" ".join(secrets.choice(words) for _ in range(24)))'
  ```

  Generate a separate passphrase for `root` and for the new user. When embedding them in the remote script, POSIX-shell-quote each full 24-word string (spaces included) the same way as git name/email — ordinary unquoted substitution will split on spaces.

- Propagate failures: run remote scripts with `set -eu` (or stricter); on any failure stop, report the failing stage, and do **not** proceed to sshd/firewall hardening.
- Use whatever non-interactive SSH auth is available (agent key, `sshpass`, `expect`, a Python SSH library, an interactive prompt — any agent environment differs). Never put a password in a tracked file or echo it into the remote shell history; pass secrets to the remote host over stdin or via a base64-encoded script sent as one SSH command.
- Treat GitHub profile fields as untrusted input. When building remote shell commands, shell-quote each field as a single argument (for example, with local `shlex.quote`); never interpolate raw profile values into shell source.
- Verify the SSH host key on first connect (`StrictHostKeyChecking=accept-new`) and note the host's address/fingerprint in the report.
- Idempotent: re-running must not duplicate keys or users, and must back up any config it replaces (timestamped suffix).

## Workflow

### 1. Fetch GitHub keys and git identity

```sh
curl -fsS "https://api.github.com/users/<github-user>"
curl -fsS "https://github.com/<github-user>.keys"
```

- Stop and ask if the user has **no** public SSH keys — there would be no way in after hardening.
- Record each key's fingerprint locally: `ssh-keygen -lf <keyfile>`.
- Email resolution, first hit wins; never invent an address:
  1. Profile `email` field (often `null`).
  2. Commit author email: list recently pushed repos (`/users/<u>/repos?sort=pushed`), then `/repos/<owner>/<repo>/commits?author=<u>` and use the author name/email from recent commits (also visible in `https://github.com/<owner>/<repo>/commit/<sha>.patch`).
  3. Fallback `<id>+<login>@users.noreply.github.com` (numeric `id` from the profile) — say in the report that this fallback was used.
- Git name: profile `name`, else the login.

### 2. Probe the server (initial root access)

Confirm it is actually Debian and see what tooling exists before planning installs:

```sh
cat /etc/os-release        # ID=debian required; stop and ask if not
id; uname -a; ip -brief address; ss -tlnp
for program in sudo git nft systemctl sshd useradd chpasswd visudo; do
    command -v "$program" || :
done
head -20 /etc/ssh/sshd_config   # note the sshd_config.d Include line
```

Minimal Debian images often lack `sudo`, `git`, `nftables`, and any firewall frontend (`ufw`/`iptables`). Use nftables directly; do not install a firewall frontend just for this.

### 3. Create the user (before any hardening)

Remote script (as root, `set -eu`, non-interactive apt):

```sh
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y sudo git nftables

id <user> >/dev/null 2>&1 || useradd -m -s /bin/bash <user>
printf 'root:%s\n'    <shell-quoted-root-passphrase>    | chpasswd
printf '<user>:%s\n'  <shell-quoted-user-passphrase>    | chpasswd

install -d -m 700 -o <user> -g <user> /home/<user>/.ssh
backup_suffix=$(date -u +%Y%m%dT%H%M%SZ)
github_keys=<shell-quoted-server-local-github-key-file>
authorized_keys=/home/<user>/.ssh/authorized_keys
authorized_keys_source=$(mktemp "$authorized_keys.source.XXXXXX")
authorized_keys_new=$(mktemp "$authorized_keys.new.XXXXXX")
trap 'rm -f "$github_keys" "$authorized_keys_source" "$authorized_keys_new"' HUP INT TERM EXIT
if [ -f "$authorized_keys" ]; then
    cat "$authorized_keys" > "$authorized_keys_source"
    # keep the first appended key on its own line when the file lacks a trailing newline
    if [ -n "$(tail -c 1 "$authorized_keys_source")" ]; then
        printf '\n' >> "$authorized_keys_source"
    fi
else
    : > "$authorized_keys_source"
fi
cat "$github_keys" >> "$authorized_keys_source"
LC_ALL=C sort -u "$authorized_keys_source" > "$authorized_keys_new"
if [ -f "$authorized_keys" ]; then
    cp -p "$authorized_keys" "$authorized_keys.$backup_suffix"
fi
chown <user>:<user> "$authorized_keys_new"
chmod 600 "$authorized_keys_new"
mv "$authorized_keys_new" "$authorized_keys"
rm -f "$github_keys" "$authorized_keys_source"

sudoers_file=/etc/sudoers.d/<user>
if [ -e "$sudoers_file" ]; then
    cp -p "$sudoers_file" "$sudoers_file.$backup_suffix"
fi
sudoers_candidate=/etc/sudoers.d/.<user>.tmp
printf '<user> ALL=(ALL:ALL) NOPASSWD: ALL\n' > "$sudoers_candidate"
chmod 440 "$sudoers_candidate"
visudo -cf "$sudoers_candidate" || { rm -f "$sudoers_candidate"; exit 1; }
mv "$sudoers_candidate" "$sudoers_file"

git_name=<shell-quoted-git-name>
git_email=<shell-quoted-git-email>
sudo -H -u <user> git config --global user.name "$git_name"
sudo -H -u <user> git config --global user.email "$git_email"
```

Copy the validated GitHub keys to a server-local temporary file and substitute its POSIX-shell-quoted path for `<shell-quoted-server-local-github-key-file>`. The atomic merge keeps existing recovery keys, backs up a pre-existing `authorized_keys` with a timestamped suffix before replacing it, and removes duplicate complete key lines on re-runs. Replace `<shell-quoted-root-passphrase>`, `<shell-quoted-user-passphrase>`, `<shell-quoted-git-name>`, and `<shell-quoted-git-email>` above with POSIX-shell-quoted values when building the remote script. A passphrase must be one argument because it contains spaces; its words are `[a-z]+`, so one pair of single quotes (what `shlex.quote` emits) is enough. Git name and email can contain apostrophes, so the same POSIX quoting is required there: wrapping the raw value in one pair of single quotes is not sufficient.

Verify in the same stage — all must pass before continuing:

```sh
ssh-keygen -lf /home/<user>/.ssh/authorized_keys   # matches GitHub fingerprints
su - <user> -c 'sudo -n id && git config --global --list'
# sudo -n id must print uid=0(root); home/.ssh perms 700, authorized_keys 600
```

Before continuing, open a second SSH connection as `<user>` using the installed key while keeping the initial root session open. If the agent does not have the matching private key, ask the owner to test and wait for confirmation. Do not proceed until this login succeeds.

Before applying the firewall, verify that this key login succeeds explicitly on port 22:

```sh
ssh -o BatchMode=yes -p 22 <user>@<host> true
```

If the server currently uses a custom SSH port, do not apply a firewall that allows only port 22: pause and ask before changing that intentional setting. If the user confirms migration, make SSH listen on 22 and repeat the port-22 key-login test while the initial session remains open.

Note: both passwords are already rotated here, so later root logins use the **new** root password.

### 4. Firewall (nftables)

Write and syntax-check a candidate before replacing `/etc/nftables.conf`; back up a pre-existing configuration with a timestamped suffix:

```sh
nft_config=/etc/nftables.conf
nft_candidate=$(mktemp /etc/nftables.conf.XXXXXX)
cat > "$nft_candidate" <<'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif "lo" accept
        ct state established,related accept
        ct state invalid drop
        ip protocol icmp accept
        ip6 nexthdr icmpv6 accept
        tcp dport { 22, 80, 443 } ct state new accept
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
    }
    chain output {
        type filter hook output priority filter; policy accept;
    }
}
EOF

if ! nft -c -f "$nft_candidate"; then
    rm -f "$nft_candidate"
    exit 1
fi
backup_suffix=$(date -u +%Y%m%dT%H%M%SZ)
if [ -e "$nft_config" ]; then
    cp -p "$nft_config" "$nft_config.$backup_suffix" || { rm -f "$nft_candidate"; exit 1; }
fi
chmod 644 "$nft_candidate"
mv "$nft_candidate" "$nft_config"
```

```sh
systemctl enable nftables
systemctl restart nftables     # applies the new file even when the unit was already active
nft list ruleset
```

### 5. Harden sshd

Do this last, and only after step 3 verification passed. Drop-in (`00-` sorts first among files matched by `Include /etc/ssh/sshd_config.d/*.conf`; OpenSSH is first-match-wins. A matching directive before the `Include` in the main file still takes precedence, so verify the effective settings below):

```sh
hardening_file=/etc/ssh/sshd_config.d/00-hardening.conf
hardening_candidate=$(mktemp /etc/ssh/sshd_config.d/.00-hardening.conf.XXXXXX)
backup_suffix=$(date -u +%Y%m%dT%H%M%SZ)
hardening_backup=
if [ -e "$hardening_file" ]; then
    hardening_backup="$hardening_file.$backup_suffix"
    cp -p "$hardening_file" "$hardening_backup"
fi

restore_hardening_file() {
    if [ -n "$hardening_backup" ]; then
        cp -p "$hardening_backup" "$hardening_file"
    else
        rm -f "$hardening_file"
    fi
}

if ! cat > "$hardening_candidate" <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
EOF
then
    rm -f "$hardening_candidate"
    exit 1
fi
chmod 644 "$hardening_candidate"
mv "$hardening_candidate" "$hardening_file"
```

```sh
if ! sshd -t; then
    restore_hardening_file
    exit 1
fi
if ! effective=$(sshd -T); then
    restore_hardening_file
    exit 1
fi
for required in \
    'permitrootlogin no' \
    'passwordauthentication no' \
    'kbdinteractiveauthentication no' \
    'pubkeyauthentication yes' \
    'permitemptypasswords no'
do
    if ! printf '%s\n' "$effective" | grep -Fx "$required"; then
        restore_hardening_file
        exit 1
    fi
done
systemctl reload ssh           # Debian unit is "ssh"; reload, not restart
```

### 6. Verify from outside and inside

External (from the agent's machine):

- `ssh root@<host>` → `Permission denied (publickey)` (no password prompt offered).
- Password auth attempt as root → same.
- `ssh <user>@<host>` with the matching private key, if the agent has it → works. If the agent does not hold the private key, do **not** claim this test passed; say the owner must test `ssh <user>@<host>` first thing.
- Port probe: `22` open; `80`/`443` reachable-but-refused when no web server is installed yet (firewall allows, nothing listening); a few other ports (e.g. `25, 8080, 3306`) time out (dropped).

Internal (via the new user's key login, if available):

```sh
id; sudo -n id
sudo nft list ruleset; sudo sshd -T | grep -iE '^(permitrootlogin|passwordauthentication)'
systemctl is-enabled nftables ssh; systemctl is-active nftables ssh
git config --global --list; ls -ld ~/.ssh; cat ~/.ssh/authorized_keys
```

Gotcha: a port can look "open" from the agent's network yet never reach the box (e.g. outbound SMTP interception makes `25/tcp` connect with no banner). Before reporting a firewall hole, confirm server-side with `ss -tlnp` / live `ss -tn` while probing.

### 7. Report and clean up

Report briefly:

- Server: hostname, IP, Debian version
- New passwords for `root` and `<user>`, with "store these in a password manager" (old root password is dead; root password is now console/recovery only)
- Git identity used and where the email came from (profile / commit author / noreply fallback)
- Key fingerprint(s) installed
- Files changed: `/etc/sudoers.d/<user>`, `/etc/ssh/sshd_config.d/00-hardening.conf`, `/etc/nftables.conf`, `~<user>/.gitconfig`; include timestamped backup paths for every pre-existing configuration replaced
- Verification results, including anything **not** tested (e.g. key login if the agent lacks the private key)
- Caveats: nothing listens on 80/443 yet; the user should confirm `ssh <user>@<host>` works before closing any existing sessions

Delete local temp files containing secrets.
