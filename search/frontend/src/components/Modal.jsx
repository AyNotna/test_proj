import { useState } from "react";

function Modal({ query, onSave, onClose }) {
  const isEditing = !!query;

  const [form, setForm] = useState({
    name: query?.name || "",
    status: query?.status || "active",
    deadline: query?.deadline
      ? new Date(query.deadline).toISOString().slice(0, 16)
      : "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!form.name.trim()) {
      alert("Введите название");
      return;
    }
    if (!form.deadline) {
      alert("Выберите дату завершения");
      return;
    }

    onSave({
      name: form.name.trim(),
      status: form.status,
      deadline: new Date(form.deadline).toISOString(),
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{isEditing ? "Редактировать запрос" : "Новый поисковый запрос"}</h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Название *</label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Например: Поиск квартир в центре"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Статус</label>
            <select name="status" value={form.status} onChange={handleChange}>
              <option value="active">Активен</option>
              <option value="inactive">Не активен</option>
            </select>
          </div>

          <div className="form-group">
            <label>Дата завершения (дедлайн) *</label>
            <input
              type="datetime-local"
              name="deadline"
              value={form.deadline}
              onChange={handleChange}
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Отмена
            </button>
            <button type="submit" className="btn btn-primary">
              {isEditing ? "Сохранить" : "Создать"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Modal;
