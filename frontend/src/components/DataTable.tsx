import { useState, useMemo, type ReactNode } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight, Search, Download, Check } from 'lucide-react';

export interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  width?: string;
  render?: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  searchable?: boolean;
  searchPlaceholder?: string;
  selectable?: boolean;
  onSelectionChange?: (selected: T[]) => void;
  exportable?: boolean;
  exportFilename?: string;
  pageSize?: number;
  emptyIcon?: string;
  emptyTitle?: string;
  emptyDescription?: string;
  onRowClick?: (row: T) => void;
  getRowId?: (row: T) => string;
}

export default function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  searchable = false,
  searchPlaceholder = 'Search...',
  selectable = false,
  onSelectionChange,
  exportable = false,
  exportFilename = 'export',
  pageSize = 10,
  emptyIcon = '📄',
  emptyTitle = 'No data',
  emptyDescription = 'No records found.',
  onRowClick,
  getRowId,
}: DataTableProps<T>) {
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const filtered = useMemo(() => {
    if (!search) return data;
    const q = search.toLowerCase();
    return data.filter(row =>
      columns.some(col => {
        const val = row[col.key];
        return val !== null && val !== undefined && String(val).toLowerCase().includes(q);
      }),
    );
  }, [data, search, columns]);

  const sorted = useMemo(() => {
    if (!sortKey) return filtered;
    return [...filtered].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortOrder === 'asc' ? cmp : -cmp;
    });
  }, [filtered, sortKey, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const paged = sorted.slice(page * pageSize, (page + 1) * pageSize);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortOrder('asc');
    }
    setPage(0);
  };

  const handleSelectAll = () => {
    if (selected.size === paged.length) {
      setSelected(new Set());
    } else {
      const ids = paged.map((row, i) => getRowId?.(row) ?? String(i));
      setSelected(new Set(ids));
    }
    onSelectionChange?.(selected.size === paged.length ? [] : paged);
  };

  const handleSelectRow = (id: string) => {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelected(next);
    onSelectionChange?.(data.filter((row, i) => next.has(getRowId?.(row) ?? String(i))));
  };

  const handleExport = () => {
    const headers = columns.map(c => c.header);
    const rows = sorted.map(row => columns.map(c => String(row[c.key] ?? '')));
    const csv = [headers.join(','), ...rows.map(r => r.map(v => `"${v.replace(/"/g, '""')}"`).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${exportFilename}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderSortIcon = (key: string, sortable?: boolean) => {
    if (!sortable) return null;
    if (sortKey !== key) return <ChevronsUpDown size={14} className="sort-icon" />;
    return sortOrder === 'asc' ? <ChevronUp size={14} className="sort-icon active" /> : <ChevronDown size={14} className="sort-icon active" />;
  };

  return (
    <div className="data-table-wrapper">
      {(searchable || exportable || selectable) && (
        <div className="data-table-toolbar">
          {searchable && (
            <div className="data-table-search">
              <Search size={16} />
              <input
                type="text"
                placeholder={searchPlaceholder}
                value={search}
                onChange={e => { setSearch(e.target.value); setPage(0); }}
              />
            </div>
          )}
          <div className="data-table-toolbar-actions">
            {selectable && selected.size > 0 && (
              <span className="data-table-selection-count">{selected.size} selected</span>
            )}
            {exportable && (
              <button className="btn btn-secondary btn-sm" onClick={handleExport}>
                <Download size={14} /> Export
              </button>
            )}
          </div>
        </div>
      )}

      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {selectable && (
                <th style={{ width: 40 }}>
                  <div
                    className={`data-table-checkbox ${selected.size === paged.length && paged.length > 0 ? 'checked' : ''}`}
                    onClick={handleSelectAll}
                  >
                    {selected.size === paged.length && paged.length > 0 && <Check size={12} />}
                  </div>
                </th>
              )}
              {columns.map(col => (
                <th
                  key={col.key}
                  style={col.width ? { width: col.width } : undefined}
                  className={col.sortable ? 'sortable' : ''}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <span className="th-content">
                    {col.header}
                    {renderSortIcon(col.key, col.sortable)}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length + (selectable ? 1 : 0)} className="data-table-loading">
                  <div className="spinner" />
                </td>
              </tr>
            ) : paged.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (selectable ? 1 : 0)} className="data-table-empty">
                  <div className="empty-state">
                    <div className="empty-icon">{emptyIcon}</div>
                    <h3>{emptyTitle}</h3>
                    <p>{emptyDescription}</p>
                  </div>
                </td>
              </tr>
            ) : (
              paged.map((row, i) => {
                const id = getRowId?.(row) ?? String(i);
                return (
                  <tr
                    key={id}
                    className={onRowClick ? 'clickable' : ''}
                    onClick={() => onRowClick?.(row)}
                  >
                    {selectable && (
                      <td onClick={e => e.stopPropagation()}>
                        <div
                          className={`data-table-checkbox ${selected.has(id) ? 'checked' : ''}`}
                          onClick={() => handleSelectRow(id)}
                        >
                          {selected.has(id) && <Check size={12} />}
                        </div>
                      </td>
                    )}
                    {columns.map(col => (
                      <td key={col.key}>
                        {col.render ? col.render(row) : String(row[col.key] ?? '—')}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="data-table-pagination">
          <span className="data-table-info">
            Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
          </span>
          <div className="data-table-pages">
            <button
              className="btn btn-secondary btn-sm btn-icon"
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
            >
              <ChevronLeft size={14} />
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const start = Math.max(0, Math.min(page - 2, totalPages - 5));
              const p = start + i;
              return (
                <button
                  key={p}
                  className={`btn btn-sm ${p === page ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setPage(p)}
                >
                  {p + 1}
                </button>
              );
            })}
            <button
              className="btn btn-secondary btn-sm btn-icon"
              disabled={page >= totalPages - 1}
              onClick={() => setPage(p => p + 1)}
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
