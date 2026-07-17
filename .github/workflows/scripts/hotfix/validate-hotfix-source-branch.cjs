module.exports = async ({ github, context, core }) => {
  const sourceBranch = process.env.SOURCE_BRANCH;
  const targetBranch = process.env.TARGET_BRANCH;
  const { owner, repo } = context.repo;

  if (!sourceBranch || !targetBranch) {
    core.setFailed("source_branch and target_branch are required.");
    return;
  }

  if (sourceBranch === targetBranch) {
    core.setFailed("source_branch and target_branch must be different.");
    return;
  }

  const { data: branch } = await github.rest.repos
    .getBranch({ owner, repo, branch: sourceBranch })
    .catch(() => ({ data: null }));

  if (!branch) {
    core.setFailed(`Source branch '${sourceBranch}' does not exist.`);
    return;
  }

  const { data: target } = await github.rest.repos
    .getBranch({ owner, repo, branch: targetBranch })
    .catch(() => ({ data: null }));

  if (!target) {
    core.setFailed(`Target branch '${targetBranch}' does not exist.`);
    return;
  }

  const prs = await github.paginate(github.rest.pulls.list, {
    owner,
    repo,
    state: "open",
    head: `${owner}:${sourceBranch}`,
    per_page: 100,
  });

  const hotfixPr = prs.find((pr) => pr.labels.some((label) => label.name.toLowerCase() === "hotfix"));

  if (!hotfixPr) {
    core.setFailed(`Branch '${sourceBranch}' does not have an open PR labeled hotfix.`);
    return;
  }

  const { data: reviews } = await github.rest.pulls.listReviews({
    owner,
    repo,
    pull_number: hotfixPr.number,
    per_page: 100,
  });

  const latestByUser = new Map();
  for (const review of reviews) {
    latestByUser.set(review.user.login, review.state);
  }

  const hasBlockingChangeRequest = [...latestByUser.values()].includes("CHANGES_REQUESTED");
  const approvalCount = [...latestByUser.values()].filter((state) => state === "APPROVED").length;

  if (hasBlockingChangeRequest) {
    core.setFailed(`PR #${hotfixPr.number} has an active CHANGES_REQUESTED review.`);
    return;
  }

  if (approvalCount < 1) {
    core.setFailed(`PR #${hotfixPr.number} must have at least one approval.`);
    return;
  }

  core.info(`Validated hotfix PR #${hotfixPr.number} from ${sourceBranch} to merge into ${targetBranch}.`);
};