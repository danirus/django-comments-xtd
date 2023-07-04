import '@testing-library/jest-dom';

global.bootstrap = {
  Tooltip: class {
    constructor(_) {}
  }
};