# write a short description of what the following routine does
# This script cleans up local git branches that have been deleted from the remote repository.
# It fetches the latest changes from the remote, identifies branches that are no longer present on the remote,
# and deletes them from the local repository.
git fetch -p

# Delete local branches that have been deleted from the remote
# The command 'git branch -vv' lists all local branches with their tracking information.
# The 'grep ': gone]' filters out branches that are no longer present on the remote.
# The 'awk '{print $1}' extracts the branch names.
# The 'git branch -D "$b"' command deletes each of these branches locally.
# The loop iterates over each branch name and deletes it.
for b in $(git branch -vv | grep ': gone]' | awk '{print $1}'); do
  git branch -D "$b"
done
