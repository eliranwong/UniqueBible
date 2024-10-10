import logging
from github import Github
from uniquebible import config
import base64


class GithubUtil:

    def __init__(self, repo=""):
        self.logger = logging.getLogger('uba')
        accessToken = config.githubAccessToken
        self.repo = None
        self.g = Github(accessToken)
        if len(repo) > 0:
            self.repo = self.g.get_repo(repo)

    def printAllPersonalRepos(self):
        if self.repo:
            for repo in self.g.get_user().get_repos():
                print(repo.name)

    def printBranches(self):
        branches = self.repo.get_branches()
        for branch in branches:
            print(branch)

    def getRepoData(self):
        branch = self.repo.get_branch(self.repo.default_branch)
        sha = branch.commit.sha
        tree = self.repo.get_git_tree(sha)
        data = {}
        for element in tree.tree:
            if ".zip" in element.path:
                file = element.path.replace(".zip", "")
                if element.type == "blob":
                    data[file] = element.sha
                else:
                    data[file] = "tree-" + element.sha
        return data

    def printContentsOfRepo(self):
        data = self.getRepoData()
        for key in data.keys():
            print("{0}:{1}".format(key, data[key]))

    def downloadFile(self, filename, sha):
        if sha.startswith("tree-"):
            sha = sha[5:]
            tree = self.repo.get_git_tree(sha)
            with open(filename, 'wb') as zipfile:
                for element in tree.tree:
                    file = self.repo.get_git_blob(element.sha)
                    decoded = base64.b64decode(file.content)
                    zipfile.write(decoded)
        else:
            file = self.repo.get_git_blob(sha)
            decoded = base64.b64decode(file.content)
            with open(filename, 'wb') as zipfile:
                zipfile.write(decoded)

    @staticmethod
    def getShortname(filename):
        if " - " in filename and filename.endswith(".commentary"):
            shortFilename = filename[:filename.find(" - ")]
        elif " -- " in filename:
            shortFilename = filename[:filename.find(" -- ")]
        else:
            shortFilename = filename
        return shortFilename


if __name__ == "__main__":
    from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo

    # github = GithubUtil(GitHubRepoInfo.bibles[0])
    # github.printContentsOfRepo()

    github = GithubUtil("otseng/UBA-Wiki")
    github.printContentsOfRepo()
    github.printBranches()
    github.downloadFile("file.zip", "tree-2c12af93b64436c86869f58ce3e7b4ce24dd5772")

