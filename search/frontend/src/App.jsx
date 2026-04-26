import { useState, useEffect, useCallback } from "react";
import Table from "./components/Table";
import Modal from "./components/Modal";
import Pagination from "./components/Pagination";
import "./App.css";

const API_URL = "https://test-proj-v2ze.onrender.com/api/queries";

function App() {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState("created_at");
  const [order, setOrder] = useState("desc");
  const [limit] = useState(20);

  const [selectedIds, setSelectedIds] = useState([]);

  const [modalOpen, setModalOpen] = useState(false);
  const [editingQuery, setEditingQuery] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(
        `${API_URL}/?page=${page}&limit=${limit}&sort=${sort}&order=${order}`,
      );
      const json = await res.json();
      setData(json.data);
      setTotal(json.total);
    } catch (error) {
      console.error("Ошибка загрузки:", error);
    }
  }, [page, limit, sort, order]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSort = (field) => {
    if (sort === field) {
      setOrder(order === "asc" ? "desc" : "asc");
    } else {
      setSort(field);
      setOrder("asc");
    }
    setPage(1);
  };

  const handleSelect = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const handleSelectAll = () => {
    if (selectedIds.length === data.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(data.map((item) => item.id));
    }
  };

  const handleCreate = () => {
    setEditingQuery(null);
    setModalOpen(true);
  };

  const handleEdit = (query) => {
    setEditingQuery(query);
    setModalOpen(true);
  };

  const handleSave = async (formData) => {
    try {
      if (editingQuery) {
        await fetch(`${API_URL}/${editingQuery.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });
      } else {
        await fetch(`${API_URL}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });
      }
      setModalOpen(false);
      setEditingQuery(null);
      fetchData();
    } catch (error) {
      console.error("Ошибка сохранения:", error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Удалить запись?")) return;
    try {
      await fetch(`${API_URL}/${id}`, { method: "DELETE" });
      fetchData();
    } catch (error) {
      console.error("Ошибка удаления:", error);
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedIds.length === 0) {
      alert("Не выбрано ни одной записи");
      return;
    }
    if (!window.confirm(`Удалить ${selectedIds.length} записей?`)) return;
    try {
      await fetch(`${API_URL}/delete-many`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(selectedIds),
      });
      setSelectedIds([]);
      fetchData();
    } catch (error) {
      console.error("Ошибка удаления:", error);
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="app">
      <h1>запросы</h1>

      <div className="toolbar">
        <button className="btn btn-primary" onClick={handleCreate}>
          Новый запрос
        </button>
        <button
          className="btn btn-danger"
          onClick={handleDeleteSelected}
          disabled={selectedIds.length === 0}
        >
          Удалить выбранные ({selectedIds.length})
        </button>
      </div>

      <Table
        data={data}
        sort={sort}
        order={order}
        onSort={handleSort}
        selectedIds={selectedIds}
        onSelect={handleSelect}
        onSelectAll={handleSelectAll}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

      {modalOpen && (
        <Modal
          query={editingQuery}
          onSave={handleSave}
          onClose={() => {
            setModalOpen(false);
            setEditingQuery(null);
          }}
        />
      )}
    </div>
  );
}

export default App;
