import { create } from 'zustand';

export const useStore = create((set) => ({
  websites: [],
  setWebsites: (websites) => set({ websites }),
  addWebsite: (website) =>
    set((state) => ({
      websites: [...state.websites, website],
    })),
  removeWebsite: (id) =>
    set((state) => ({
      websites: state.websites.filter((w) => w.id !== id),
    })),
}));
