export default function BrandMark({ className = "h-9 w-9" }) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded-xl bg-primary text-white shadow-soft ${className}`}
      aria-hidden="true"
    >
      <svg viewBox="0 0 32 32" className="h-[62%] w-[62%]" fill="none">
        <path
          d="M8 22V10h6.2c3.4 0 5.5 1.8 5.5 4.6 0 1.8-.9 3.2-2.5 4l3.3 3.4h-3.4l-2.9-3.1H11V22H8Zm3-5.4h3c1.6 0 2.5-.8 2.5-2s-.9-2-2.5-2h-3v4Z"
          fill="currentColor"
        />
        <circle cx="23.5" cy="9.5" r="1.6" fill="currentColor" opacity="0.85" />
        <circle cx="26.2" cy="14.2" r="1.2" fill="currentColor" opacity="0.65" />
        <path
          d="M23.5 11.2v2.2M24.8 13.4l1 1"
          stroke="currentColor"
          strokeWidth="1.4"
          strokeLinecap="round"
          opacity="0.8"
        />
      </svg>
    </span>
  );
}
