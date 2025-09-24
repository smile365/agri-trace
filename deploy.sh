rsync -avz --exclude-from='.gitignore' \
  --exclude='docs/' \
  --exclude='tests/' \
  --exclude='.git/' \
  --exclude='.gitignore' \
  --exclude='*.md' \
  --include='./start.sh' \
  ./ pxact:/root/projects/farm/