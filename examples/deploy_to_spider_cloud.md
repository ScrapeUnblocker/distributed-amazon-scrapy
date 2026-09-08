# Deploy to Spider Cloud

Once the spiders run locally, deploying the same project to
[ScrapeUnblocker Spider Cloud](https://docs.scrapeunblocker.com/spider-cloud/?utm_source=github&utm_medium=integration&utm_campaign=example-repos)
lets you run them at scale on a schedule, with routing applied automatically.
**Nothing about this project needs to change** - `scrapy.cfg` and the spiders are
all Spider Cloud needs.

## Option A - CLI

```bash
pip install scrapeunblocker-cloud

export SU_CLOUD_TOKEN="suc_..."     # from your dashboard
export SU_CLOUD_ORG="your-org"
export SU_CLOUD_PROJECT="amazon"

su-cloud login          # stores credentials in ~/.su-cloud.json
su-cloud deploy         # builds and uploads the current directory
```

Then start a run for a spider from the **Spiders** tab, or from the CLI, passing
the same `-a` arguments you use locally (e.g. `keyword`, `pages`).

## Option B - Dashboard (git)

1. Create a project at **app.scrapeunblocker.com/dashboard/spiders** and select
   your git source (GitHub / GitLab).
2. Connect this repository.
3. On the **Deploys** tab, pick a branch and press **Deploy**.
4. On the **Spiders** tab, pick a spider, set the routing mode to route through
   ScrapeUnblocker, and press **Run**.

Requests marked `meta={"unblock": True}` (which every request in this project is)
are routed for you - no key handling, no middleware config.

## Schedules

Add a schedule from the dashboard to run a spider on a cron cadence and send
results to a destination (webhook, storage bucket, etc.). See the
[schedules docs](https://docs.scrapeunblocker.com/spider-cloud/schedules?utm_source=github&utm_medium=integration&utm_campaign=example-repos).
