import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders go button', () => {
  render(<App />);
  const el = screen.getByText(/Go/i);
  expect(el).toBeInTheDocument();
});
