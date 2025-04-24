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

## Download logs from emr
```sh
aws s3 cp s3://flight-emr/logs/j-28AW3RV826BE/containers/ ./logs/ --recursive --region us-east-1
aws s3 cp s3://flight-emr/logs/j-55EEI978OJYX/containers/ ./logs/ --recursive --region us-east-1

```

## Monolithic Chart Serving

[Prompt](https://chatgpt.com/c/6808578e-6558-8010-bba1-e2d0c460553a)

## Clean up git branches
```sh
git fetch -p  # Prune tracking branches that have been removed from remote

# Delete all local branches whose remote is gone
for b in $(git branch -vv | grep ': gone]' | awk '{print $1}'); do
  git branch -D "$b"
done
```
