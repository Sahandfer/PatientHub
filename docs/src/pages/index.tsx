import type { ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/">
            Get Started 🚀
          </Link>
          {/* <Link
            className="button button--outline button--secondary button--lg"
            style={{ marginLeft: '1rem' }}
            to="/docs/components/overview">
            Explore 📚
          </Link> */}
        </div>
      </div>
    </header>
  );
}

function QuickStart() {
  return (
    <section className={styles.quickStart}>
      <div className="container">
        <Heading as="h2" className="text--center margin-bottom--lg">
          Quick Start
        </Heading>
        <div className="row">
          <div className="col col--6 col--offset-3">
            <pre className={styles.codeBlock}>
              <code>
                {`# Clone the repository
git clone https://github.com/Sahandfer/Patient-Simulation.git
cd Patient-Simulation

# Install dependencies
uv sync

# Activate the environment
source .venv/bin/activate

# Run a simulation
uv run python -m examples.simulate \\
  client=patientPsi \\
  therapist=CBT`}
              </code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}

function SupportedMethods() {
  const methods = [
    { name: 'ConsistentMI', venue: 'ACL 2025', focus: 'Motivational Interviewing' },
    { name: 'Eeyore', venue: 'ACL 2025', focus: 'Depression Simulation' },
    { name: 'PatientPsi', venue: 'EMNLP 2024', focus: 'CBT Training' },
    { name: 'SimPatient', venue: 'CHI 2025', focus: 'Alcohol Misuse' },
    { name: 'RoleplayDoh', venue: 'EMNLP 2024', focus: 'Counseling' },
    { name: 'SAPS', venue: 'ArXiv 2024', focus: 'Clinical Diagnosis' },
  ];

  return (
    <section className={styles.methods}>
      <div className="container">
        <Heading as="h2" className="text--center margin-bottom--lg">
          11 Research-Backed Methods
        </Heading>
        <div className="row">
          {methods.map((method, idx) => (
            <div key={idx} className="col col--4 margin-bottom--md">
              <div className={styles.methodCard}>
                <Heading as="h4">{method.name}</Heading>
                <p className={styles.venue}>{method.venue}</p>
                <p>{method.focus}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="text--center margin-top--lg">
          <Link
            className="button button--primary button--lg"
            to="/docs/components/overview">
            View All Methods →
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title="PatientHub"
      description="A unified framework for LLM-based patient simulation in mental health training and research">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <QuickStart />
        <SupportedMethods />
      </main>
    </Layout>
  );
}
