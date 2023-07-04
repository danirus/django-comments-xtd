import { getCookie } from "../src/lib.js";


describe("Test 'getCookie' from lib.js", () => {
  it("Returns undefined", () => {
    const result = getCookie("csrftoken");
    expect(result).toBeUndefined();
  });

  it("Returns the value of the cookie", () => {
    const cookie_name = "csrftoken";
    const cookie_value = "abcd1234";
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: `${cookie_name}=${cookie_value}`
    });

    const result = getCookie(cookie_name);
    expect(result).toBe(cookie_value);
  });

  it("Returns the value of the cookie, even when padded with spaces", () => {
    const cookie_name = "csrftoken";
    const cookie_value = "abcd1234";
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: `  ${cookie_name}=${cookie_value}  `
    });

    const result = getCookie(cookie_name);
    expect(result).toBe(cookie_value);
  });
});
