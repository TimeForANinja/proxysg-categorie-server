/**
 * Utility interface for generalizing data thats referencing other entries
 * e.g.: a commit or atomic that has a reference to the url/category/token it was created for
 */

export interface ICommit {
    author: string;
    description: string;
    head: IStateTreeRootNode;
    parent_commit_hash: string;
}

export interface IStateTreeRootNode {
    categories: string[];
    tokens: string[];
}
