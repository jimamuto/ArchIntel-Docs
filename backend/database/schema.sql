-- Create table for storing user-edited documentation
create table if not exists file_documentation (
  id uuid default uuid_generate_v4() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  file_path text not null,
  content text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(project_id, file_path)
);

-- Enable Row Level Security (RLS)
alter table file_documentation enable row level security;

-- Create policy to allow all access (since this is a local/personal tool for now)
-- In a production environment, you would restrict this based on user auth
create policy "Allow all access" on file_documentation for all using (true) with check (true);
