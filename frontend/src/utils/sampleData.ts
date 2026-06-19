import type { ContactInput } from '../types/api';

export const sampleContact: ContactInput = {
  name: "Aarav Mehta",
  role: "VP Sales",
  company: "Acme Corp",
  location: "Bengaluru, India",
  linkedin_profile: {
    headline: "VP Sales at Acme Corp | Enterprise SaaS | GTM Leadership",
    about: "I enjoy building high-performing revenue teams and scaling SaaS businesses across India and Southeast Asia.",
    experience: [
      {
        title: "VP Sales",
        company: "Acme Corp",
        description: "Leading enterprise sales, strategic accounts, and GTM expansion."
      },
      {
        title: "Regional Sales Director",
        company: "Salesforce",
        description: "Managed enterprise accounts across BFSI and retail."
      }
    ],
    recent_posts: [
      "Great sales teams are built on trust, coaching, and consistency.",
      "India's SaaS ecosystem is entering an exciting new phase.",
      "Still recovering from yesterday's India vs Australia match. What a game!"
    ],
    recent_comments: [
      "Completely agree, pipeline discipline matters more than heroic end-of-quarter selling.",
      "Loved this take on customer-led growth.",
      "Cricket teaches leadership better than most management books."
    ],
    engaged_topics: [
      "Cricket",
      "Revenue leadership",
      "SaaS GTM",
      "Customer-led growth",
      "Team building"
    ]
  },
  relationship_context: {
    relationship_type: "Prospective customer",
    last_interaction: "Positive discovery call last week",
    business_goal: "Nurture relationship before follow-up meeting"
  },
  gift_context: {
    occasion: "Post-meeting thank you",
    budget_min: 100,
    budget_max: 5000,
    currency: "INR",
    country: "India",
    tone: "warm"
  }
};

export const sampleBulkContacts: ContactInput[] = [
  sampleContact,
  {
    name: "Priya Raman",
    role: "Head of Engineering",
    company: "Northbridge Systems",
    location: "Chennai, India",
    linkedin_profile: {
      headline: "Head of Engineering at Northbridge Systems | Distributed Systems | Mentor",
      about: "Passionate about building resilient distributed systems and mentoring early-career engineers.",
      experience: [
        {
          title: "Head of Engineering",
          company: "Northbridge Systems",
          description: "Leading platform and infrastructure engineering."
        }
      ],
      recent_posts: [
        "Finished an amazing trail run this weekend, nothing clears the mind like it.",
        "Mentoring junior engineers is the most rewarding part of my week.",
        "Excited about the new Rust adoption across our backend teams."
      ],
      recent_comments: [
        "Trail running shoes make a huge difference, happy to share recommendations.",
        "Completely agree on investing in junior engineer growth."
      ],
      engaged_topics: [
        "Distributed systems",
        "Trail running",
        "Engineering mentorship",
        "Rust programming"
      ]
    },
    relationship_context: {
      relationship_type: "Long-term client",
      last_interaction: "Renewed annual contract last month",
      business_goal: "Strengthen long-term partnership"
    },
    gift_context: {
      occasion: "Contract renewal appreciation",
      budget_min: 4000,
      budget_max: 7000,
      currency: "INR",
      country: "India",
      tone: "formal"
    }
  }
];
