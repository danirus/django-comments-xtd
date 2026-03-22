/// <reference types="cypress" />

declare namespace Cypress {
    interface Chainable<Subject> {
        /**
         * Run an Management command.
         *
         * @example
         * cy.manage()
         */
        manage(command: string, parameters?: string[]): Chainable<any>;
        /**
         * Get the CSRF Token.
         *
         * @example
         * cy.csrfToken()
         */
        csrfToken(): Chainable<any>;
        /**
         * Run the python manage.py migrate command
         *
         * @example
         * cy.migrate()
         */
        migrate(): Chainable<any>;
        /**
         * Create a new user.
         *
         * @example
         * cy.createUser()
         */
        createUser(attributes: object): Chainable<any>;
    }
}