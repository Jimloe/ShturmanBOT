# ShturmanBOT
The async praw rebuilt version to assist with moderation of the /r/EscapefromTarkov subreddit.

## Commands
### remove_post
**Aliases**: remove, r

**Description**: This will remove a post when provided a reason and a URL. Use !reasons to see a list of removal reasonsShturman will confirm whether or not you want to remove the post.

**Switches**: Rule# - 1-8

URL - Any valid post URL

**Syntax**: !remove Rule# URL

**Example**: !remove 8 https://old.reddit.com/r/EscapefromTarkov/comments/o5u5mn/event_overview_megathread/

### media_spam

**Aliases**: ms.

**Description**: This will enable or disable checking posts for Rule 5 violations (48hrs)

**Switches**: runprogram - enable/disable

ignoremods - true/false

action - report/remove

**Syntax**: !ms (enbale/disable) (true/false) (report/remove)

**Example**: !ms enable true report

### watchqueue

**Aliases**: wq.

**Description**: This will enable or disable watching the moderator queues and sending alerts.

**Switches**: runprogram - enable/disable

**Syntax**: !wq (enbale/disable)

**Example**: !wq enable

### devtracker

**Aliases**: dt.

**Description**: This will enable or disable watching for dev activity on the sub.

**Switches**: runprogram - enable/disable

**Syntax**: !dt (enbale/disable)

**Example**: !dt enable

### turnoff

**Aliases**: turnoff, shutdown

**Description**: This will stop ShturmanBOT from running, only use in case he's being naughty. Currently broken due to server permissions.

**Syntax**: !shutdown

### info

**Description**: This will show some information about the user calling the command

**Syntax**: !info

### backup_eft

**Aliases**: bu, backup

**Description**: This will backup the Automoderator, CSS configurations, and CSS images locally.

**Switches**: Backup Images true/false. Will enable or disable CSS image backup. Off by default.

**Syntax**: !backup true - Backs up configs & images

**Syntax**: !backup - Backs up configs only.
