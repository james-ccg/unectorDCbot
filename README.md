# Unector

Unector is a Python 3.12 Discord bot built with `discord.py`, SQLite, and modular Cogs.

## Included in this first milestone

- Slash command `/unector status`
- SQLite storage for processed news items
- GamerPower free-game polling with required source attribution
- Steam news polling through the public ISteamNews endpoint
- Optional role ping, one discussion thread per published item, duplicate prevention
- `.env` configuration, Ruff linting, and pytest tests
- No `Administrator` permission requirement

This is a working starter for **Milestone 1**. LFG, temporary voice rooms, events, welcome/logging, protection, levels, and Steam profile linking are documented as later modules and are not claimed to be implemented yet.

## Requirements

- Windows 10/11 (or another OS with Python 3.12)
- Python 3.12.x
- A Discord application and bot token
- Internet access while the bot is running

## Windows setup (Command Prompt)

1. Extract this folder to a location such as `D:\project\Unector`.
2. Open Command Prompt in that folder.
3. Check Python:

   ```bat
   py -3.12 --version
   ```

4. Create and activate a virtual environment:

   ```bat
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bat
   python -m pip install --upgrade pip
   pip install -e ".[dev]"
   ```

6. Copy `.env.example` to `.env`, then fill the values described below.
7. Start the bot:

   ```bat
   python -m unector
   ```

## Discord Developer Portal

1. Create an application named **Unector**.
2. Open **Bot**, create/reset the bot token, and keep it private.
3. In **Bot > Privileged Gateway Intents**, enable **Server Members Intent** only if you later enable member join/welcome features. This first milestone does not need it.
4. Under **OAuth2 > URL Generator**, select `bot` and `applications.commands`.
5. Grant only the channel and thread permissions required for the features you enable. Do not grant `Administrator`.
6. Invite the bot to your test server. Make sure its role is above any role it needs to mention/manage.
7. For `/unector status`, `Send Messages` is enough. For media posts, allow `View Channel`, `Send Messages`, `Embed Links`, `Create Public Threads`, `Send Messages in Threads`; `Manage Threads` is only needed for broader thread management.
8. Copy the target `#game-news` channel ID (enable Developer Mode in Discord, right-click the channel, Copy Channel ID) into `GAME_NEWS_CHANNEL_ID`.

## `.env` configuration

- `DISCORD_TOKEN`: bot token from Developer Portal. Never share it or commit `.env`.
- `DISCORD_GUILD_ID`: optional test server ID. If set, slash commands sync to that server for quick testing; otherwise commands sync globally and may take time to appear.
- `GAME_NEWS_CHANNEL_ID`: channel receiving media posts.
- `GAME_NEWS_ROLE_ID`: optional ping role ID. Empty means no role ping.
- `STEAM_APP_IDS`: comma-separated numeric Steam app IDs. Defaults to `730` (Counter-Strike 2); replace as desired.
- `MEDIA_POLL_MINUTES`: polling interval, default 30 minutes.
- `DATABASE_PATH`: SQLite file location, default `data/unector.sqlite3`.

## Test and quality checks

```bat
ruff check .
pytest
```

Both should pass before you push changes. Tests run without a Discord token and do not contact external APIs.

## GitHub without accidental secrets

Create a **new empty repository** named `Unector`, then from this project folder:

```bat
git init
git add .
git status
```

Review `git status` carefully. Confirm `.env`, `.venv`, and `data/unector.sqlite3` are not listed. Then:

```bat
git commit -m "Initialize Unector bot"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/Unector.git
git push -u origin main
```

Replace `YOUR-ACCOUNT` with your GitHub username. Do not upload the `.zip` containing secrets or the `.env` file. If a token is accidentally committed, revoke/reset it in Discord Developer Portal immediately; deleting it in a later commit does not remove it from Git history.

### About Contributors and attribution

GitHub's Contributors graph is based on commit history and account-associated author emails. If you want your own legitimate contributions not to be linked to your public profile, configure a GitHub-provided noreply email before making commits and verify your account's email/privacy settings. Do not impersonate another author or falsify commit history. A repository owner cannot guarantee that GitHub will show no contributors, and forks, pull requests, commits, and repository activity may expose contribution information.

No tool can guarantee a project has no detectable AI assistance or metadata traces. This project avoids embedding personal names in source files and excludes local secrets and generated runtime files, but that is not a guarantee of provenance anonymity.

## Operational notes

- GamerPower requires an active hyperlink/attribution to GamerPower.com; the embed includes it.
- The polling loop is deliberately slow and uses request timeouts. Do not increase the frequency unnecessarily.
- External API data can change shape or become unavailable. Errors are logged and the bot retries on the next cycle.
- Steam news posts are fetched per configured app ID. Keep the list short to avoid unnecessary requests.
- Use a test channel before enabling automatic public posts.

## Roadmap

1. **Milestone 1:** core, SQLite, slash status, free games + Steam news, threads and optional ping.
2. **Milestone 2:** `/lfg` with Join/Leave controls, expiry, and thread.
3. **Milestone 3:** join-to-create temporary voice rooms.
4. **Milestone 4:** Discord Scheduled Events and event request flow.
5. **Milestone 5:** welcome messages, `/roles`, moderation log.
6. **Milestone 6:** raid signals and warning history.
7. **Later:** levels, starboard, Steam profile linking.

Build each module separately and test it in a private test server before enabling it in the community.


## Media post quality and publishing panel

Media posts include giveaway images when the source provides them. Each published post attempts to add 👍 🔥 ❤️ reactions and creates a discussion thread with a starter message. Discord permissions must allow sending messages, embedding links, adding reactions, and creating public threads. Some Steam articles do not provide a usable image, so those posts may remain text-only.

A small optional publishing website is included. It is disabled by default. To enable it, set `WEB_PANEL_ENABLED=1`, configure `WEB_PANEL_USER` and a unique `WEB_PANEL_PASSWORD` of at least 16 characters in `.env`, then restart the bot. Open `http://127.0.0.1:8787` on the same computer and authenticate with those credentials. It lists text channels in `DISCORD_GUILD_ID` (or the first connected server if that ID is blank) where the bot can send messages and embeds. The panel can publish a title, body, image URL, video link, and optional reactions.

**Security:** keep `WEB_PANEL_HOST=127.0.0.1` unless you know how to securely expose a web service. Do not port-forward this panel directly to the public internet. For remote access, use a VPN or a properly configured HTTPS reverse proxy and strong credentials. Discord bot token and panel password belong only in `.env`.
