# CC Swtich

# Codex & DeepSeek

API请求网址（完整）

    https://api.deepseek.com/chat/completions

测试请求

    curl https://api.deepseek.com/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer sk-8c2f65f2415d4813885788ad79a203c8" \
      -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}'