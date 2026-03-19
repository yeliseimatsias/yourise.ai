import '../styles/Button.css';

function Button({ variant = 'gray', className = '', children, ...props }) {
   
  const baseClass = 'button';
  const variantClass = `button--${variant}`;

  return (
    <button
      className={`${baseClass} ${variantClass} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}
export default Button