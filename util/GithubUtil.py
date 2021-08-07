import logging
from github import Github
import config
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
                data[file] = element.sha
        return data

    def printContentsOfRepo(self):
        data = self.getRepoData()
        for key in data.keys():
            print("{0}:{1}".format(key, data[key]))

    def downloadFile(self, filename, sha):
        file = self.repo.get_git_blob(sha)
        decoded = base64.b64decode(file.content)
        with open(filename, 'wb') as zipfile:
            zipfile.write(decoded)

    @staticmethod
    def getShortname(filename):
        if " - " in filename and filename.endswith(".commentary"):
            shortFilename = filename[:filename.find(" - ")]
        else:
            shortFilename = filename
        return shortFilename


if __name__ == "__main__":
    from util.GitHubRepoInfo import GitHubRepoInfo

    github = GithubUtil(GitHubRepoInfo.bibles[0])
    github.printContentsOfRepo()

    # github = GithubUtil("otseng/UniqueBible_Commentaries")
    # github.printContentsOfRepo()
    # github.downloadFile("test.zip", "1274eccd33476b0e4716b41e292d50ad601715c8")

