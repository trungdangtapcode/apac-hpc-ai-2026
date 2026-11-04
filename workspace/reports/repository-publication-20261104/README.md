# Repository visibility change

On 4 November 2026, the owner explicitly requested public visibility. The GitHub CLI visibility change succeeded and an unauthenticated GitHub API request confirmed `private: false`. The canonical repository returned by GitHub is https://github.com/trungdangtapcode/apac-hpc-ai-2026; the previously configured `apac-hpc-ai-research` URL redirects there. This operation changed visibility, not the repository name.

Preflight screened all 34,044 reachable local Git blob versions (13,228,607,786 logical bytes) using the existing credential signatures, including readable ZIP members up to 30 MB. No signature findings were returned. The published HPC release submission ZIP was restored from its retained object, matched to the remote SHA-256 digest and screened with no findings. No GitHub Actions runs were present. Pattern screening cannot guarantee absence of every kind of sensitive information. Existing draft releases were not published.

The owner-requested script numbering changes were not captured or committed as part of this visibility checkpoint. Slides, research jobs and authentication state were unchanged. Earlier documentation describing the repository as private is historical.
