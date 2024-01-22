# /usr/bin/env ruby
require 'json'
require 'set'

user_keys = {}
User = Struct.new(:emails, :keys)
committer_emails = `git log --since="2021-11-14" --format="%G? %aE" | grep -v "^N" | sort -u | cut -d " " -f 2`.split("\n")
committer_emails.each do |email|
  user_json = `curl -H --silent "Accept: application/vnd.github.v3+json" https://api.github.com/search/users?q=#{email}`
  username = JSON.parse(user_json)["items"]&.first&.[]("login")
  if username
    user_keys[username] ||= begin
      User.new Set.new,
        `curl --silent https://github.com/#{username}.keys`.split("\n")
    end
    user_keys[username].emails.add(email)
  end
end

user_keys.map do |username, user|
  puts "# #{username}"
  user.keys.each do |key|
    puts "#{user.emails.to_a.join(",")} #{key}"
  end
end
