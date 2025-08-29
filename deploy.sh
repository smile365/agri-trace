rsync -avz --exclude-from='.gitignore' \
  --exclude='docs/' \
  --exclude='tests/' \
  --exclude='.git/' \
  --exclude='.gitignore' \
  --exclude='*.md' \
  --exclude='*.sh' \
  ./ pxact:/root/projects/farm/