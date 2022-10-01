from datetime import datetime
from urllib import response
import requests
from requests.auth import HTTPBasicAuth
from typing import List


class Github:
    def __init__(self, token: str = None) -> None:
        self.url = "https://api.github.com/"
        self.headers = {"Authorization": f"token {token}"}

    def pulls(self, repo: str, state: str = "all") -> List[dict]:
        """Fetches a list of pull requests with status state made on the provided repo.

        Parameters
        ----------
        repo :  str
                string of format {owner}/{repository}
                    owner       -- username of owner of the repository
                    repository  -- name of the repository
        state : {\'all\', \'open\', \'closed\'}
                status of the pull request (open / closed / all)

        Returns
        -------
        data :  List[dict]
            list of pull requests where each record is a dict containing:
                \'username\' : str
                    username of the author
                \'labels\'   : List[str]
                    list of labels on the pull request

        Raises
        ------
        ValueError
            If the value of state is not \'all\', \'open\' or \'closed\'.
        RuntimeError
            If response status code from the request isn't 200.

        """

        VALID_STATES = {"all", "open", "closed"}

        state = state.lower()  # Making state case-insensitive
        if state not in VALID_STATES:
            # Raise error when invalid state
            raise ValueError(f"state: state must be one of {VALID_STATES}")

        url = f"{self.url}repos/{repo}/pulls?state={state}"
        if self.headers == None:
            response = requests.get(url)
        else:
            response = requests.get(
                url, headers=self.headers)

        if response.ok:
            data = response.json()

            # Filtering out label, datetime and author username from data
            for index in range(len(data)):
                record = dict()
                record["username"] = data[index]["user"]["login"]
                record["labels"] = [label["name"]
                                    for label in data[index]["labels"]]
                record["created_at"] = datetime.fromisoformat(
                    data[index]["created_at"][:-1] + "+00:00")

                data[index] = record

            return data
        else:
            raise RuntimeError(
                f"Error {response.status_code}: {response.json()['message']}")

    def user(self, username: str) -> dict:
        """Fetches github user details of the provided username."""
        url = f"{self.url}users/{username}"

        user_info = {}
        if self.headers == None:
            response = requests.get(url)
        else:
            response = requests.get(
                url, headers=self.headers)

        if response.ok:
            data = response.json()

            # Filtering out only required information
            user_info["username"] = data["login"]
            user_info["name"] = data["name"]
            user_info["avatar_url"] = data["avatar_url"]
            user_info["url"] = data["html_url"]
            return user_info
        else:
            raise RuntimeError(
                f"Error {response.status_code}: {response.json()['message']}")

    def repo(self, repo: str) -> dict:
        """Fetches details of the provided repo."""
        url = f"{self.url}repos/{repo}"

        repo_info = {}
        if self.headers == None:
            response = requests.get(url)
        else:
            response = requests.get(
                url, headers=self.headers)

        if response.ok:
            data = response.json()

            # Filtering out only required information
            repo_info["name"] = data["name"]
            repo_info["full_name"] = data["full_name"]
            repo_info["description"] = data["description"]
            repo_info["url"] = data["html_url"]
            repo_info["clone_url"] = data["clone_url"]
            return repo_info
        else:
            raise RuntimeError(
                f"Error {response.status_code}: {response.json()['message']}")

    def repo_list(self, org: str, topics: List[str] = None) -> List[str]:
        url = f"{self.url}users/{org}/repos?per_page=100"

        repos = []
        page = 1

        while True:
            if self.headers == None:
                response = requests.get(f"{url}&page={page}")
            else:
                response = requests.get(
                    f"{url}&page={page}", headers=self.headers)
            repo_data = response.json()
            if repo_data == []:  # Terminate the loop if no data in the page
                break
            for repo in repo_data:
                topics_url = f"{self.url}repos/{repo['full_name']}/topics"
                if self.headers == None:
                    topics_data = requests.get(topics_url).json()["names"]
                else:
                    topics_data = requests.get(
                        topics_url, headers=self.headers).json()['names']
                if set(topics).issubset(set(topics_data)):
                    repos.append(repo["full_name"])
            page += 1
        return repos


if __name__ == "__main__":
    pass