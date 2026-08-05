export interface User {
  email: string;
  name: string;
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  fullWidth?: boolean;
  children: React.ReactNode;
}

export interface StatCardProps {
  label: string;
  value: string | number;
  textColor?: string;
}

export interface ScraperItem {
  id: string;
  title: string;
  description: string;
  lastRun: string;
  status: 'Active' | 'Inactive';
  type: 'amazon' | 'daraz' | 'linkedin' | 'news';
}

export interface JobItem {
  id: string;
  scraper: string;
  status: 'Running' | 'Queued' | 'Completed' | 'Failed';
  progress: string;
  time: string;
}

export interface ResultItem {
  id: string;
  title: string;
  price: string;
  site: string;
  timestamp: string;
}