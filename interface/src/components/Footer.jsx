import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors duration-300 mb-8">
          Commencer maintenant
        </button>
        <p className="text-gray-400">© 2024 Textra-Health. Tous droits réservés.</p>
      </div>
    </footer>
  );
};

export default Footer;