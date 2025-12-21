-- Create table for storing discussions (PRs, Issues)
create table if not exists discussions (
  id uuid default uuid_generate_v4() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  source text not null check (source in ('github_pr', 'github_issue')),
  external_id text not null, -- ID from GitHub (e.g. issue number or node_id)
  title text not null,
  body text,
  author text,
  url text,
  created_at timestamp with time zone not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(project_id, source, external_id)
);

-- Create table for linking discussions to code entities
create table if not exists discussion_links (
  id uuid default uuid_generate_v4() primary key,
  discussion_id uuid references discussions(id) on delete cascade not null,
  file_path text,
  commit_hash text,
  unique(discussion_id, file_path, commit_hash)
);

-- Enable RLS
alter table discussions enable row level security;
alter table discussion_links enable row level security;

-- Policies (Allow all for MVP)
create policy "Allow all access" on discussions for all using (true) with check (true);
create policy "Allow all access" on discussion_links for all using (true) with check (true);
