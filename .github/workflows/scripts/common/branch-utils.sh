#!/usr/bin/env bash
set -euo pipefail

branch_utils_emit() {
    local key="$1"
    local value="$2"

    if [[ -n "${GITHUB_ENV:-}" ]]; then
        printf '%s=%s\n' "$key" "$value" >>"$GITHUB_ENV"
    fi

    if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
        printf '%s=%s\n' "$key" "$value" >>"$GITHUB_OUTPUT"
    fi
}

branch_utils_target_branch() {
    if [[ -n "${TARGET_BRANCH:-}" ]]; then
        printf '%s\n' "$TARGET_BRANCH"
    elif [[ -n "${GITHUB_BASE_REF:-}" ]]; then
        printf '%s\n' "$GITHUB_BASE_REF"
    else
        printf '%s\n' "${GITHUB_REF_NAME:-dev}"
    fi
}

branch_utils_source_branch() {
    if [[ -n "${SOURCE_BRANCH:-}" ]]; then
        printf '%s\n' "$SOURCE_BRANCH"
    elif [[ -n "${GITHUB_HEAD_REF:-}" ]]; then
        printf '%s\n' "$GITHUB_HEAD_REF"
    else
        printf '%s\n' "${GITHUB_REF_NAME:-dev}"
    fi
}

branch_utils_target_sha() {
    git rev-parse HEAD
}

branch_utils_source_sha() {
    if [[ -n "${SOURCE_SHA:-}" ]]; then
        printf '%s\n' "$SOURCE_SHA"
        return
    fi

    if [[ -n "${GITHUB_HEAD_REF:-}" ]]; then
        git fetch origin "${GITHUB_HEAD_REF}:refs/remotes/origin/${GITHUB_HEAD_REF}" >/dev/null 2>&1 || true
        if git rev-parse --verify "refs/remotes/origin/${GITHUB_HEAD_REF}" >/dev/null 2>&1; then
            git rev-parse "refs/remotes/origin/${GITHUB_HEAD_REF}"
            return
        fi
    fi

    if git rev-parse HEAD^2 >/dev/null 2>&1; then
        git rev-parse HEAD^2
    else
        git rev-parse HEAD
    fi
}

branch_utils_export_context() {
    local target_branch source_branch target_sha source_sha

    target_branch="$(branch_utils_target_branch)"
    source_branch="$(branch_utils_source_branch)"
    target_sha="$(branch_utils_target_sha)"
    source_sha="$(branch_utils_source_sha)"

    branch_utils_emit TARGET_BRANCH "$target_branch"
    branch_utils_emit SOURCE_BRANCH "$source_branch"
    branch_utils_emit TARGET_SHA "$target_sha"
    branch_utils_emit SOURCE_SHA "$source_sha"
}

branch_utils_validate_source_branch() {
    local target_branch source_branch

    target_branch="${1:-$(branch_utils_target_branch)}"
    source_branch="$(branch_utils_source_branch)"

    case "$target_branch" in
    dev)
        if [[ ! "$source_branch" =~ ^(feature|hotfix|version-sync|dev-version)- ]]; then
            echo "Invalid source branch for dev: $source_branch"
            exit 1
        fi
        ;;
    staging)
        if [[ ! "$source_branch" =~ ^(pre-release|hotfix)- ]]; then
            echo "Invalid source branch for staging: $source_branch"
            exit 1
        fi
        ;;
    prod)
        if [[ "$source_branch" != "staging" ]]; then
            echo "Invalid source branch for prod: $source_branch"
            exit 1
        fi
        ;;
    ua)
        if [[ "$source_branch" != "dev" ]]; then
            echo "Invalid source branch for ua: $source_branch"
            exit 1
        fi
        ;;
    *)
        echo "No validation configured for target branch: $target_branch"
        ;;
    esac
}

branch_utils_latest_tag() {
    local pattern="$1"
    git tag --list "$pattern" --sort=-v:refname | head -n 1
}

branch_utils_parse_version() {
    local version="$1"
    version="${version#v}"
    version="${version#alpha-version-}"
    version="${version#version-}"
    version="${version#dev-version-}"
    version="${version%_update}"
    printf '%s\n' "$version"
}

branch_utils_increment_version() {
    local version="$1"
    local bump_type="${2:-PATCH}"
    local major minor patch

    IFS='.' read -r major minor patch <<<"${version#v}"
    major="${major:-0}"
    minor="${minor:-0}"
    patch="${patch:-0}"

    case "$bump_type" in
    MAJOR)
        major=$((major + 1))
        minor=0
        patch=0
        ;;
    MINOR)
        minor=$((minor + 1))
        patch=0
        ;;
    PATCH | *)
        patch=$((patch + 1))
        ;;
    esac

    printf '%s.%s.%s\n' "$major" "$minor" "$patch"
}

branch_utils_tag_for_dev() {
    local source_branch="$1"

    case "$source_branch" in
    feature-* | hotfix-*)
        printf '%s\n' "$source_branch"
        ;;
    version-sync-*)
        printf 'dev-version-%s\n' "${source_branch#version-sync-}"
        ;;
    dev-version-*)
        printf '%s\n' "${source_branch%_update}"
        ;;
    *)
        echo "Cannot derive tag from source branch: $source_branch"
        exit 1
        ;;
    esac
}

branch_utils_tag_for_staging() {
    local bump_type="${TAG_BUMP:-PATCH}"
    local latest_alpha latest_version version

    latest_alpha="$(branch_utils_latest_tag 'alpha-version-*')"
    latest_version="$(branch_utils_latest_tag 'version-*')"

    if [[ -n "$latest_alpha" ]]; then
        version="$(branch_utils_parse_version "$latest_alpha")"
    elif [[ -n "$latest_version" ]]; then
        version="$(branch_utils_parse_version "$latest_version")"
    else
        version="0.0.0"
    fi

    printf 'alpha-version-%s\n' "$(branch_utils_increment_version "$version" "$bump_type")"
}

branch_utils_tag_for_prod() {
    local latest_alpha latest_version version

    latest_alpha="$(branch_utils_latest_tag 'alpha-version-*')"
    if [[ -n "$latest_alpha" ]]; then
        version="$(branch_utils_parse_version "$latest_alpha")"
        printf 'version-%s\n' "$version"
        return
    fi

    latest_version="$(branch_utils_latest_tag 'version-*')"
    if [[ -n "$latest_version" ]]; then
        printf '%s\n' "$latest_version"
    else
        printf 'version-0.0.0\n'
    fi
}

branch_utils_create_and_push_tag() {
    local target_branch source_branch commit_sha tag_name

    target_branch="${1:-$(branch_utils_target_branch)}"
    source_branch="$(branch_utils_source_branch)"
    commit_sha="$(branch_utils_target_sha)"

    case "$target_branch" in
    dev)
        tag_name="$(branch_utils_tag_for_dev "$source_branch")"
        ;;
    staging)
        tag_name="$(branch_utils_tag_for_staging)"
        ;;
    prod)
        tag_name="$(branch_utils_tag_for_prod)"
        ;;
    *)
        echo "Tagging is not configured for target branch: $target_branch"
        exit 1
        ;;
    esac

    git tag "$tag_name" "$commit_sha"
    git push origin "$tag_name"

    branch_utils_emit TAG_NAME "$tag_name"
    branch_utils_emit TAG_SHA "$commit_sha"

    printf '%s\n' "$tag_name"
}
