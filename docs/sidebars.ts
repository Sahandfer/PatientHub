/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'User Guide',
      items: [
        'guide/simulations',
        'guide/batch-processing',
        'guide/evaluation',
        'guide/web-demo',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/clients',
        'api/therapists',
        'api/evaluators',
        'api/events',
      ],
    },
    {
      type: 'category',
      label: 'Supported Methods',
      items: [
        'methods/overview',
        'methods/patientpsi',
        'methods/consistentmi',
        'methods/eeyore',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/new-agents',
        'contributing/new-evaluators',
      ],
    },
  ],
};

module.exports = sidebars;