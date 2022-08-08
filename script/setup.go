package main

import (
	"fmt"
	"os"
	"path/filepath"
)

func main() {
	fmt.Println("#!/bin/sh")
	filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
		if err != nil {
			fmt.Fprintf(os.Stderr, "failed to access %q: %v\n", path, err)
			return err
		}
		if info.IsDir() {
			if info.Name() == ".git" || info.Name() == "script" {
				return filepath.SkipDir
			}
			return nil
		}
		if info.Name() == "README.md" {
			return nil
		}
		dest := "$HOME/" + path
		fmt.Printf("mkdir -p `dirname %q`\n", dest)
		fmt.Printf("install -p %q %q\n", path, dest)
		return nil
	})
}
