import { useEffect, useMemo, useRef, useState } from "react";

/** Strip combining marks for accent-insensitive match (é → e). */
function fold(text) {
  return String(text || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

/**
 * Typeahead hospital picker.
 * Suggestions appear only after the user types (≥1 character).
 * Selecting a suggestion sets the hospital UUID via onChange(id).
 */
export default function HospitalSearch({
  hospitals = [],
  value,
  onChange,
  required = false,
  id = "hospital",
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  const selected = useMemo(
    () => hospitals.find((h) => String(h.id) === String(value)) || null,
    [hospitals, value],
  );

  // Keep input label in sync when parent clears / sets value externally.
  useEffect(() => {
    if (selected) {
      setQuery(selected.name);
    } else if (!value) {
      setQuery("");
    }
  }, [selected, value]);

  useEffect(() => {
    function onDocClick(event) {
      if (!rootRef.current?.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const suggestions = useMemo(() => {
    const q = fold(query).trim();
    if (q.length < 1) return [];
    return hospitals.filter((h) => {
      const hay = fold(`${h.name} ${h.city || ""}`);
      return hay.includes(q);
    });
  }, [hospitals, query]);

  function handleInputChange(event) {
    const next = event.target.value;
    setQuery(next);
    setOpen(true);
    // Typing invalidates prior selection unless text still matches selected name.
    if (selected && next !== selected.name) {
      onChange("");
    }
  }

  function pick(hospital) {
    setQuery(hospital.name);
    onChange(String(hospital.id));
    setOpen(false);
  }

  const showList = open && fold(query).trim().length >= 1;

  return (
    <div className="relative" ref={rootRef}>
      <input
        id={id}
        type="text"
        className="field-input"
        value={query}
        onChange={handleInputChange}
        onFocus={() => setOpen(true)}
        placeholder="Tapez le nom de l’hôpital"
        autoComplete="off"
        role="combobox"
        aria-expanded={showList}
        aria-controls={`${id}-list`}
        aria-autocomplete="list"
        required={required && !value}
      />
      {/* Hidden field so native form required can still see a value when selected */}
      <input type="hidden" name={id} value={value || ""} required={required} />

      {fold(query).trim().length === 0 ? (
        <p className="mt-1 text-xs text-accent">
          Tapez le nom de l’hôpital pour afficher les suggestions.
        </p>
      ) : null}

      {showList ? (
        <ul
          id={`${id}-list`}
          role="listbox"
          className="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-2xl border border-light bg-white py-1 shadow-card"
        >
          {suggestions.length === 0 ? (
            <li className="px-4 py-3 text-sm text-accent">
              Aucun établissement reconnu ne correspond.
            </li>
          ) : (
            suggestions.map((hospital) => (
              <li key={hospital.id} role="option">
                <button
                  type="button"
                  className="flex w-full flex-col items-start px-4 py-2.5 text-left text-sm text-secondary transition hover:bg-primary/5"
                  onClick={() => pick(hospital)}
                >
                  <span className="font-semibold">{hospital.name}</span>
                  {hospital.city ? (
                    <span className="text-xs text-accent">{hospital.city}</span>
                  ) : null}
                </button>
              </li>
            ))
          )}
        </ul>
      ) : null}
    </div>
  );
}
