# Dynamo DB

resource "aws_dynamodb_table" "games_items" {
  name           = "${local.service_name}-game-items"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "item_id"

  attribute {
    name = "item_id"
    type = "S"
  }
}
