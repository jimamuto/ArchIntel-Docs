-- Add user_id to projects to enable multitenancy
ALTER TABLE projects ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_documentation ENABLE ROW LEVEL SECURITY;
ALTER TABLE discussions ENABLE ROW LEVEL SECURITY;
ALTER TABLE discussion_links ENABLE ROW LEVEL SECURITY;

-- Create Policies for Projects
CREATE POLICY "Users can view their own projects" ON projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own projects" ON projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own projects" ON projects
    FOR DELETE USING (auth.uid() = user_id);

-- Create Policies for Files (linked via project_id)
CREATE POLICY "Users can view files in their projects" ON files
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = files.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can modify files in their projects" ON files
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = files.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- Create Policies for Documentation
CREATE POLICY "Users can manage docs in their projects" ON file_documentation
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = file_documentation.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- Create Policies for Discussions
CREATE POLICY "Users can view discussions in their projects" ON discussions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = discussions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage discussions in their projects" ON discussions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = discussions.project_id
            AND projects.user_id = auth.uid()
        )
    );
