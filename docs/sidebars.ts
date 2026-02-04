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
      label: 'Supported Agents',
      items: [
        'methods/overview',
        {
          type: 'category',
          label: 'Clients',
          items: [
            'methods/saps',
            'methods/consistentmi',
            'methods/eeyore',
            'methods/annaagent',
            'methods/adaptivevp',
            'methods/simpatient',
            'methods/talkdep',
            'methods/clientcast',
            'methods/psyche',
            'methods/patientpsi',
            'methods/roleplaydoh',
          ],
        },
        'methods/therapists',
        'methods/evaluators',
        'methods/npcs',
        'methods/generators',
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
