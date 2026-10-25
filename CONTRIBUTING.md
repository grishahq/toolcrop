# Contributing to ToolCrop

File a minimal trusted task specification and candidate sequence for a false accept/reject. Describe expected intent separately from generated calls. Never add provider credentials or real customer records to fixtures. Keep held-out tasks separate from prompt tuning and training.

Use the README's offline test/lint commands before a pull request. Add meaningful tests when changing tool semantics, oracle checks, import boundaries or export contracts. Specify new scenarios independently of the planner. Preserve Curator attribution and APIs; upstream updates should be reviewed monthly with the recipe and relevant baseline checks rerun. Scope live/GPU/provider tests explicitly, and never report skipped or blocked checks as passing. Distribution changes must retain LICENSE/NOTICE and clean-install evidence.
