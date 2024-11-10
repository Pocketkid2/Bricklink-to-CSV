defmodule Brickyui.Repo do
  use Ecto.Repo,
    otp_app: :brickyui,
    adapter: Ecto.Adapters.SQLite3
end
