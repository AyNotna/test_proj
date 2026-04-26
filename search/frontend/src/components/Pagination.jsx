function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;

    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);

    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  };

  return (
    <div className="pagination">
      <button onClick={() => onPageChange(1)} disabled={page === 1}>
        ««
      </button>
      <button onClick={() => onPageChange(page - 1)} disabled={page === 1}>
        «
      </button>

      {getPageNumbers().map((num) => (
        <button
          key={num}
          onClick={() => onPageChange(num)}
          className={num === page ? "active" : ""}
        >
          {num}
        </button>
      ))}

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page === totalPages}
      >
        »
      </button>
      <button
        onClick={() => onPageChange(totalPages)}
        disabled={page === totalPages}
      >
        »»
      </button>

      <span>
        Страница {page} из {totalPages}
      </span>
    </div>
  );
}

export default Pagination;
