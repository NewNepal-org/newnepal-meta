I need to update the README.md for the meta repo. Let's start with a plan on how devs should use it.

1. There are two kinds of Jawafdehi contributors: Team members and Open source contributors.

Team members will use the Jawafdehi meta repo, which will help them expedite with all the information necessary for GenAI clients.
Open Source contributors may just pull the specific service repository, and create a PR, without ever worrying about this meta repo.

NepalEntityService is the primary open source service that we are targeting will have a great use case. Hence, NES docs should be placed in /docs folder, which has already been symlinked to metarepo /docs/nes folder.

We need to re-organize the kiro specs, which should be moved to the meta repo sttering.

We should update all the README for all packages, inform them about this meta repo which is intended for enriching the context for GenAI clients.

Furthermore, this meta repo should also show more details about the org.

The project board: https://trello.com/b/zSNsFJvU/jawafdehiorg

The website: beta.jawafdehi.org

