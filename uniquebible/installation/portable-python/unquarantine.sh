find . -type file -exec  xattr -d com.apple.quarantine  {} \;
