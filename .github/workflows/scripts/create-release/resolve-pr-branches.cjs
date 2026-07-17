const { execSync } = require("node:child_process");

module.exports = async ({ github, context, core }) => {
  const { owner, repo } = context.repo;
  const tags = (process.env.TAGS_CSV || "")
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  const safeRef = (value) => /^[A-Za-z0-9._/-]+$/.test(value);
  const tagCommits = new Map();

  for (const tag of tags) {
    if (!safeRef(tag)) {
      core.setFailed(`Invalid tag name: ${tag}`);
      return;
    }

    const commit = execSync(`git rev-list -n 1 refs/tags/${tag}`, { encoding: "utf8" }).trim();
    tagCommits.set(tag, commit);
  }

  const pulls = await github.paginate(github.rest.pulls.list, {
    owner,
    repo,
    state: "open",
    per_page: 100,
  });

  const matchedBranches = new Set();

  for (const pr of pulls) {
    if (!pr.head?.repo || pr.head.repo.full_name !== `${owner}/${repo}`) {
      continue;
    }

    const branch = pr.head.ref;
    if (!safeRef(branch)) {
      core.info(`Skipping unsafe branch ref: ${branch}`);
      continue;
    }

    try {
      execSync(`git fetch --no-tags origin ${branch}`, { stdio: "ignore" });
    } catch {
      core.info(`Could not fetch branch '${branch}', skipping.`);
      continue;
    }

    for (const commit of tagCommits.values()) {
      try {
        execSync(`git merge-base --is-ancestor ${commit} origin/${branch}`, { stdio: "ignore" });
        matchedBranches.add(branch);
        break;
      } catch {
        // Commit is not reachable from this PR branch.
      }
    }
  }

  const branches = [...matchedBranches].sort();
  if (branches.length === 0) {
    core.setFailed("No open PR branches found that contain any of the provided tags.");
    return;
  }

  core.info(`Matched PR branches: ${branches.join(", ")}`);
  core.setOutput("branches_csv", branches.join(","));
};