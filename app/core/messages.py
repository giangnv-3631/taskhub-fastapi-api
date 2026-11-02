USER_NOT_FOUND = "User not found"
PROJECT_NOT_FOUND = "Project not found"
TASK_NOT_FOUND = "Task not found"
COMMENT_NOT_FOUND = "Comment not found"

ASSIGNEE_NOT_FOUND = "Assignee does not exist"
ASSIGNEE_INACTIVE = "Assignee is inactive"
TAG_REFERENCE_NOT_FOUND = "One or more tags do not exist"

USER_ALREADY_EXISTS = "Email or username already registered"
USER_HAS_RELATED_DATA = "User still owns projects, tasks or comments"

INVALID_CREDENTIALS = "Incorrect username or password"
INVALID_TOKEN = "Could not validate credentials"
INACTIVE_USER = "Inactive user"
ADMIN_ROLE_REQUIRED = "Admin role required"
PROJECT_MANAGER_ROLE_REQUIRED = "Project manager or admin role required"
PROJECT_PERMISSION_DENIED = "Only the project owner or an admin can manage this project"
CANNOT_DELETE_SELF = "You cannot delete your own account"
TASK_UPDATE_DENIED = "Only the assignee, the project owner or an admin can update this task"
COMMENT_UPDATE_DENIED = "Only the comment author can edit this comment"
COMMENT_DELETE_DENIED = "Only the comment author, the project owner or an admin can delete this comment"

TASK_ALREADY_BOOKMARKED = "Task already bookmarked"

FIELD_CANNOT_BE_NULL = "{field} cannot be null"
DUE_DATE_IN_PAST = "due_date cannot be in the past"

NEW_COMMENT_EMAIL_SUBJECT = "New comment on task: {task_title}"
NEW_COMMENT_EMAIL_BODY = "{author} commented on \"{task_title}\":\n\n{content}"
EMAIL_LOGGED = "SMTP not configured, email to %s | %s\n%s"
EMAIL_SEND_FAILED = "Failed to send email to %s"

INTERNAL_SERVER_ERROR = "Internal server error"
UNHANDLED_ERROR_LOG = "Unhandled error on %s %s"
