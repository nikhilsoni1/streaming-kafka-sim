## Important Commands

### List tree structure of a directory
```sh
tree <directory_path> -L 2 | tee -a tree.txt  
tree db -L 2 | tee -a tree.txt  
```

## Packaging db
```sh
cd db
rm -rf build/ dist/ *.egg-info
python -m build --sdist
```

## Refresh elephant01
```sh
./scripts/cloud-db/refresh-env.sh scripts/cloud-db/cloud-dev.env
```

## Setting up env
```sh
source scripts/set_env.sh .env
source scripts/set_env.sh scripts/cloud-db/cloud-dev.env
env | grep ^DATABASE_
```