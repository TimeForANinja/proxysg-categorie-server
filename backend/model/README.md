# DB Layout

Core
  |
  Type:LUT
  |
Tag
  |
Commit (author, description, head, parent)
  |
Root-Tree (categories, tokens)
  |            |                   |
  |            Type:List           Type:List
  Type:List    |                   |
  |            |                 URL (ID, value)
  |            |
  |          Category (ID, Name, members)
  |
Token (ID, value, Categories, Description)
