-- SpinalSurgery Research Platform Database Schema
-- Version: 1.0.0
-- Database: PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'researcher', 'viewer')),
    institution VARCHAR(255),
    department VARCHAR(255),
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research projects table
CREATE TABLE research_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    field VARCHAR(255) NOT NULL,
    keywords TEXT[],
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'published')),
    start_date DATE,
    end_date DATE,
    irb_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paper sources (journals, institutions) table
CREATE TABLE paper_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('journal', 'institution', 'database', 'conference')),
    url VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    access_type VARCHAR(50) CHECK (access_type IN ('open', 'subscription', 'institutional', 'request')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research collaborators table
CREATE TABLE collaborators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES research_projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    institution VARCHAR(255),
    department VARCHAR(255),
    role VARCHAR(100),
    contribution TEXT,
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Papers table (both own and referenced)
CREATE TABLE papers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES research_projects(id) ON DELETE SET NULL,
    source_id UUID REFERENCES paper_sources(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    authors TEXT[],
    abstract TEXT,
    content TEXT,
    doi VARCHAR(255),
    pmid VARCHAR(50),
    publication_year INTEGER,
    publication_date DATE,
    journal_name VARCHAR(255),
    volume VARCHAR(50),
    issue VARCHAR(50),
    pages VARCHAR(50),
    paper_type VARCHAR(50) CHECK (paper_type IN ('original', 'review', 'case_report', 'meta_analysis', 'editorial')),
    is_own_paper BOOLEAN DEFAULT false,
    presentation_date DATE,
    presentation_venue VARCHAR(255),
    presentation_type VARCHAR(50) CHECK (presentation_type IN ('oral', 'poster', 'keynote')),
    file_path VARCHAR(500),
    url VARCHAR(500),
    citation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personal paper portfolio table
CREATE TABLE paper_portfolio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    category VARCHAR(100),
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, paper_id)
);

-- Patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES research_projects(id) ON DELETE CASCADE,
    patient_code VARCHAR(100) NOT NULL,
    age INTEGER,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    bmi DECIMAL(4,2),
    diagnosis_data JSONB,
    surgery_data JSONB,
    outcome_data JSONB,
    follow_up_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, patient_code)
);

-- Statistical analyses table
CREATE TABLE statistical_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES research_projects(id) ON DELETE CASCADE,
    analysis_name VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(100),
    software_used VARCHAR(100),
    parameters JSONB,
    results JSONB,
    interpretation TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Informed consents table
CREATE TABLE informed_consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES research_projects(id) ON DELETE CASCADE,
    template_name VARCHAR(255),
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    language VARCHAR(10) DEFAULT 'ko',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI generation logs table
CREATE TABLE ai_generation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES research_projects(id) ON DELETE CASCADE,
    generation_type VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    ai_model VARCHAR(50),
    processing_time INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paper references (citation relationships)
CREATE TABLE paper_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    citing_paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    cited_paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    reference_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(citing_paper_id, cited_paper_id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_user_id ON research_projects(user_id);
CREATE INDEX idx_projects_status ON research_projects(status);
CREATE INDEX idx_papers_project_id ON papers(project_id);
CREATE INDEX idx_papers_doi ON papers(doi);
CREATE INDEX idx_papers_pmid ON papers(pmid);
CREATE INDEX idx_papers_is_own ON papers(is_own_paper);
CREATE INDEX idx_patients_project_id ON patients(project_id);
CREATE INDEX idx_collaborators_project_id ON collaborators(project_id);
CREATE INDEX idx_portfolio_user_id ON paper_portfolio(user_id);

-- Create update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON research_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_papers_updated_at BEFORE UPDATE ON papers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON paper_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();