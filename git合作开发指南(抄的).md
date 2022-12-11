# Github Pull Request 流程简述

## 我不懂编程，只是想改一点点 JSON 文件/文档等，要怎么操作？

欢迎收看 [牛牛也能看懂的 GitHub Pull Request 使用指南](https://github.com/MaaAssistantArknights/MaaAssistantArknights/blob/master/docs/2.4-%E7%BA%AF%E7%BD%91%E9%A1%B5%E7%AB%AFPR%E6%95%99%E7%A8%8B.md) （纯网页端操作）

## 我会编程，但没接触过 GitHub/C++/……，要怎么操作？

1. 如果很久以前 fork 过，先在自己仓库的 `Settings` 里，翻到最下面，删除

2. 打开主仓库，点击 `Fork`，继续点击 `Create fork`

3. clone 仓库（你自己账号下） dev 分支到本地

    ```bash
    git clone <你的仓库 git 链接> -b dev
    ```

4. 配置编程环境

    略

5. 到这里，你就可以愉快地 ~~瞎 JB 改~~ 发电了

8. 开发过程中，每一定数量，记得提交一个 commit, 别忘了写上 message  
    假如你不熟悉 git 的使用，你可能想要新建一个分支进行更改，而不是直接提交在 `dev` 上

    ```bash
    git branch your_own_branch
    git checkout your_own_branch
    ```

    这样你的提交就能在新的分支上生长，不会受到 `dev` 更新的打扰

9. 完成开发后，推送你修改过的本地分支（以 `dev` 为例）到远程（fork 的仓库）

    ```bash
    git push origin dev
    ```

8. 打开主仓库。提交一个 pull request，等待管理员通过。别忘了你是在 dev 分支上修改，别提交到 master 分支去了

11. 当 MAA 原仓库出现更改（别人做的），你可能需要把这些更改同步到你的分支
    1. 关联 MAA 原仓库

        ```bash
        git remote add upstream url
        ```

    2. 从 MAA 原仓库拉取更新

        ```bash
        git fetch upstream
        ```

    3. 变基（推荐）或者合并修改

        ```bash
        git rebase upstream/dev # 变基
        ```

        或者

        ```bash
        git merge # 合并
        ```

    4. 重复上述 7, 8, 9, 10 中的操作

或许可以直接使用 vs 自带的“Git 更改”()