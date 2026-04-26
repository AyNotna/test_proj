function Table({
  data,
  sort,
  order,
  onSort,
  selectedIds,
  onSelect,
  onSelectAll,
  onEdit,
  onDelete,
}) {
  const columns = [
    { key: "name", label: "Название" },
    { key: "created_at", label: "Создан" },
    { key: "updated_at", label: "Изменён" },
    { key: "status", label: "Статус" },
    { key: "owner", label: "Владелец" },
    { key: "deadline", label: "Дедлайн" },
    { key: "results_count", label: "Найдено" },
  ];

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatStatus = (status) => {
    if (status === "active") {
      return <span className="status-active">Активен</span>;
    }
    return <span className="status-inactive">Неактивен</span>;
  };

  const allSelected = data.length > 0 && selectedIds.length === data.length;

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>
              <input
                type="checkbox"
                checked={allSelected}
                onChange={onSelectAll}
              />
            </th>
            {columns.map((col) => (
              <th
                key={col.key}
                className="sortable"
                onClick={() => onSort(col.key)}
              >
                {col.label}
                {sort === col.key && (
                  <span> {order === "asc" ? "↑" : "↓"}</span>
                )}
              </th>
            ))}
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length + 2}
                style={{ textAlign: "center", padding: "40px", color: "#999" }}
              >
                Нет данных для отображения
              </td>
            </tr>
          ) : (
            data.map((row) => (
              <tr key={row.id} className={row.is_overdue ? "overdue" : ""}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(row.id)}
                    onChange={() => onSelect(row.id)}
                  />
                </td>
                <td>
                  {row.is_overdue && (
                    <span className="overdue-label" title="Просрочен">
                      !
                    </span>
                  )}
                  {row.name}
                </td>
                <td>{formatDate(row.created_at)}</td>
                <td>{formatDate(row.updated_at)}</td>
                <td>{formatStatus(row.status)}</td>
                <td>{row.owner}</td>
                <td>{formatDate(row.deadline)}</td>
                <td>{row.results_count.toLocaleString()}</td>
                <td>
                  <div className="actions-cell">
                    <button
                      className="icon-btn"
                      onClick={() => onEdit(row)}
                      title="Редактировать"
                    >
                      Ред
                    </button>
                    <button
                      className="icon-btn"
                      onClick={() => onDelete(row.id)}
                      title="Удалить"
                    >
                      Удл
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default Table;
