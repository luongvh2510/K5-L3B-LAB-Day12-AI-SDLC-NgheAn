#!/bin/sh
# Cài các hook của nhóm vào repo này (trỏ core.hooksPath tới .agents/hooks).
ROOT="$(git rev-parse --show-toplevel)" || exit 1
chmod +x "$ROOT/.agents/hooks/pre-push"
git -C "$ROOT" config core.hooksPath .agents/hooks
echo "Đã cài hook: core.hooksPath = .agents/hooks (pre-push chạy test trước khi đẩy)."
