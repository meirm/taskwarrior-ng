import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { clsx } from 'clsx';
import { ChevronDown, Plus, Search, X, Check } from 'lucide-react';
import { useDebounce } from '@/utils/debounce';

/**
 * ProjectSelector Component
 * 
 * A searchable dropdown component for selecting existing projects or creating new ones.
 * 
 * TESTABLE BEHAVIORS:
 * 1. Displays existing projects in a searchable dropdown
 * 2. Shows "Create new project" option when typing a non-existing project name
 * 3. Filters projects based on search input (case-insensitive)
 * 4. Supports keyboard navigation (ArrowUp, ArrowDown, Enter, Escape)
 * 5. Handles hierarchical projects with dot notation (e.g., "Work.Backend.API")
 * 6. Provides visual distinction between existing and new projects
 * 7. Closes dropdown when clicking outside or pressing Escape
 * 8. Maintains focus management for accessibility
 * 9. Debounces search input to prevent excessive filtering
 * 10. Shows selected project with check icon
 */

export interface ProjectSelectorProps {
  /** Currently selected project value */
  value?: string;
  /** Callback when project is selected or created */
  onChange: (project: string | undefined) => void;
  /** List of existing projects */
  projects: string[];
  /** Placeholder text when no project is selected */
  placeholder?: string;
  /** Label for the field */
  label?: string;
  /** Error message to display */
  error?: string;
  /** Helper text to display */
  helperText?: string;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Whether the field is required */
  required?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Field name for form integration */
  name?: string;
  /** Field ID for accessibility */
  id?: string;
}

interface ProjectOption {
  value: string;
  label: string;
  isNew?: boolean;
  level?: number;
}

const ProjectSelector: React.FC<ProjectSelectorProps> = ({
  value,
  onChange,
  projects = [],
  placeholder = "Select or create project",
  label,
  error,
  helperText,
  disabled = false,
  required = false,
  className,
  name,
  id,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const [inputValue, setInputValue] = useState(value || '');
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  
  const fieldId = id || `project-selector-${Math.random().toString(36).substr(2, 9)}`;
  
  // Debounce the search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 200);

  // Parse hierarchical projects and create options
  const projectOptions = useMemo(() => {
    const options: ProjectOption[] = [];
    
    // Add existing projects
    projects.forEach(project => {
      const level = project.split('.').length - 1;
      options.push({
        value: project,
        label: project,
        level,
      });
    });
    
    // Sort projects alphabetically with hierarchy consideration
    options.sort((a, b) => {
      const aParts = a.value.split('.');
      const bParts = b.value.split('.');
      
      for (let i = 0; i < Math.min(aParts.length, bParts.length); i++) {
        const comparison = aParts[i].localeCompare(bParts[i]);
        if (comparison !== 0) return comparison;
      }
      
      return aParts.length - bParts.length;
    });
    
    return options;
  }, [projects]);

  // Filter options based on debounced search query
  const filteredOptions = useMemo(() => {
    const query = debouncedSearchQuery.toLowerCase().trim();
    
    if (!query) {
      return projectOptions;
    }
    
    // Filter existing projects
    const filtered = projectOptions.filter(option =>
      option.value.toLowerCase().includes(query)
    );
    
    // Check if we should show "Create new" option
    const exactMatch = projectOptions.some(
      option => option.value.toLowerCase() === query
    );
    
    if (!exactMatch && query.length > 0) {
      // Add "Create new project" option at the beginning
      // Use the original searchQuery (not debounced) for immediate feedback
      filtered.unshift({
        value: searchQuery.trim(),
        label: `Create "${searchQuery.trim()}"`,
        isNew: true,
      });
    }
    
    return filtered;
  }, [debouncedSearchQuery, searchQuery, projectOptions]);

  // Handle dropdown open/close
  const handleToggleDropdown = useCallback(() => {
    if (!disabled) {
      setIsOpen(prev => !prev);
      if (!isOpen) {
        setSearchQuery('');
        setHighlightedIndex(0);
        // Focus input when opening
        setTimeout(() => inputRef.current?.focus(), 0);
      }
    }
  }, [disabled, isOpen]);

  // Handle option selection
  const handleSelectOption = useCallback((option: ProjectOption) => {
    onChange(option.value);
    setInputValue(option.value);
    setSearchQuery('');
    setIsOpen(false);
    setHighlightedIndex(0);
  }, [onChange]);

  // Handle clear selection
  const handleClear = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(undefined);
    setInputValue('');
    setSearchQuery('');
    setHighlightedIndex(0);
  }, [onChange]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < filteredOptions.length - 1 ? prev + 1 : prev
        );
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : 0);
        break;
        
      case 'Enter':
        e.preventDefault();
        if (filteredOptions[highlightedIndex]) {
          handleSelectOption(filteredOptions[highlightedIndex]);
        }
        break;
        
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setSearchQuery('');
        break;
        
      case 'Tab':
        setIsOpen(false);
        break;
    }
  }, [isOpen, filteredOptions, highlightedIndex, handleSelectOption]);

  // Handle search input change
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setHighlightedIndex(0);
  }, []);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Scroll highlighted option into view
  useEffect(() => {
    if (isOpen && listRef.current) {
      const highlightedElement = listRef.current.children[highlightedIndex] as HTMLElement;
      if (highlightedElement) {
        highlightedElement.scrollIntoView({
          block: 'nearest',
          behavior: 'smooth',
        });
      }
    }
  }, [highlightedIndex, isOpen]);

  // Update input value when value prop changes
  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  return (
    <div className={clsx('space-y-1', className)}>
      {label && (
        <label 
          htmlFor={fieldId} 
          className="block text-sm font-medium text-secondary-700"
        >
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative" ref={dropdownRef}>
        {/* Main selector button/input */}
        <div
          className={clsx(
            'relative w-full',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          {!isOpen ? (
            // Closed state - show button
            <button
              type="button"
              id={fieldId}
              name={name}
              onClick={handleToggleDropdown}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              className={clsx(
                'w-full px-3 py-2 text-left bg-white border rounded-md shadow-sm',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'disabled:bg-secondary-50 disabled:cursor-not-allowed',
                error ? 'border-error-300' : 'border-secondary-300',
                'flex items-center justify-between'
              )}
              aria-haspopup="listbox"
              aria-expanded={isOpen}
              aria-labelledby={label ? `${fieldId}-label` : undefined}
            >
              <span className={clsx(
                'block truncate',
                !inputValue && 'text-secondary-400'
              )}>
                {inputValue || placeholder}
              </span>
              <div className="flex items-center space-x-1">
                {inputValue && !disabled && (
                  <X
                    className="w-4 h-4 text-secondary-400 hover:text-secondary-600"
                    onClick={handleClear}
                  />
                )}
                <ChevronDown className="w-4 h-4 text-secondary-400" />
              </div>
            </button>
          ) : (
            // Open state - show search input
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400" />
              <input
                ref={inputRef}
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                onKeyDown={handleKeyDown}
                placeholder="Search or create project..."
                className={clsx(
                  'w-full pl-10 pr-10 py-2 bg-white border rounded-md shadow-sm',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                  error ? 'border-error-300' : 'border-secondary-300'
                )}
                aria-autocomplete="list"
                aria-controls={`${fieldId}-listbox`}
                role="combobox"
              />
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1"
              >
                <X className="w-4 h-4 text-secondary-400 hover:text-secondary-600" />
              </button>
            </div>
          )}
        </div>

        {/* Dropdown menu */}
        {isOpen && (
          <ul
            ref={listRef}
            id={`${fieldId}-listbox`}
            role="listbox"
            className={clsx(
              'absolute z-10 w-full mt-1 bg-white border border-secondary-200',
              'rounded-md shadow-lg max-h-60 overflow-auto',
              'focus:outline-none'
            )}
          >
            {filteredOptions.length === 0 ? (
              <li className="px-3 py-2 text-sm text-secondary-500">
                No projects found. Type to create a new one.
              </li>
            ) : (
              filteredOptions.map((option, index) => (
                <li
                  key={`${option.value}-${index}`}
                  role="option"
                  aria-selected={option.value === value}
                  className={clsx(
                    'relative cursor-pointer select-none py-2 pr-9',
                    'hover:bg-primary-50',
                    index === highlightedIndex && 'bg-primary-50',
                    option.value === value && 'font-medium',
                    option.level && `pl-${3 + option.level * 4}`,
                    !option.level && 'pl-3'
                  )}
                  onClick={() => handleSelectOption(option)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                >
                  <div className="flex items-center">
                    {option.isNew && (
                      <Plus className="w-4 h-4 mr-2 text-primary-600" />
                    )}
                    <span className={clsx(
                      'block truncate',
                      option.isNew && 'text-primary-600'
                    )}>
                      {option.label}
                    </span>
                  </div>
                  {option.value === value && (
                    <span className="absolute inset-y-0 right-0 flex items-center pr-3">
                      <Check className="w-4 h-4 text-primary-600" />
                    </span>
                  )}
                </li>
              ))
            )}
          </ul>
        )}
      </div>

      {/* Error and helper text */}
      {error && (
        <p className="text-sm text-error-600" role="alert">
          {error}
        </p>
      )}
      {helperText && !error && (
        <p className="text-sm text-secondary-500">
          {helperText}
        </p>
      )}
    </div>
  );
};

export default ProjectSelector;