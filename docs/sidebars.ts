/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      link: {
        type: 'doc',
        id: 'getting-started/installation',
      },
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'Components',
      link: {
        type: 'doc',
        id: 'components/overview',
      },
      items: [
        // 'components/overview',
        {
          type: 'category',
          label: 'Clients',
          link: {
            type: 'doc',
            id: 'components/clients/overview',
          },
          items: [
            'components/clients/saps',
            'components/clients/consistentmi',
            'components/clients/eeyore',
            'components/clients/annaagent',
            'components/clients/adaptivevp',
            'components/clients/simpatient',
            'components/clients/talkdep',
            'components/clients/clientcast',
            'components/clients/psyche',
            'components/clients/patientpsi',
            'components/clients/roleplaydoh',
            'components/clients/user',
          ],
        },
        {
          type: 'category',
          label: 'Therapists',
          link: {
            type: 'doc',
            id: 'components/therapists/overview',
          },
          items: [
            'components/therapists/basic',
            'components/therapists/eliza',
            'components/therapists/user',
            'components/therapists/psyche',
            'components/therapists/cami',
          ],
        },
        {
          type: 'category',
          label: 'Evaluators',
          link: {
            type: 'doc',
            id: 'components/evaluators/overview',
          },
          items: [
            'components/evaluators/llm-judge',
          ],
        },

        {
          type: 'category',
          label: 'Generators',
          link: {
            type: 'doc',
            id: 'components/generators/overview',
          },
          items: [
            'components/generators/annaagent',
            'components/generators/clientcast',
            'components/generators/psyche',
          ],
        },
        {
          type: 'category',
          label: 'Events',
          link: {
            type: 'doc',
            id: 'components/events/overview',
          },
          items: [
            'components/events/therapy-session',
          ],
        },
        {
          type: 'category',
          label: 'NPCs',
          link: {
            type: 'doc',
            id: 'components/npcs/overview',
          },
          items: [
            'components/npcs/interviewer',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Examples',
      link: {
        type: 'doc',
        id: 'guide/simulations',
      },
      items: [
        'guide/simulations',
        'guide/evaluation',
        'guide/web-demo',
      ],
    },
    // {
    //   type: 'category',
    //   label: 'Contributing',
    //   items: [
    //     'contributing/new-agents',
    //     'contributing/new-evaluators',
    //   ],
    // },
  ],
};

module.exports = sidebars;
